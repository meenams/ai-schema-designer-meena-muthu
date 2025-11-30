
import re
from typing import List, Dict, Any
import yaml
import random
from datetime import datetime, timedelta

SNAKE_CASE_PATTERN = re.compile(r"^[a-z0-9_]+$")

def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text

def _event_name(feature_name: str, action: str) -> str:
    base = _slugify(feature_name)
    action_slug = _slugify(action)
    return f"{base}__{action_slug}"

def _default_properties(action: str) -> List[Dict[str, Any]]:
    props = [
        {"name": "user_id", "type": "string", "description": "Unique identifier for the user", "required": True},
        {"name": "workspace_id", "type": "string", "description": "Workspace or account identifier", "required": True},
        {"name": "timestamp", "type": "datetime", "description": "Event timestamp in ISO 8601", "required": True},
    ]
    if "error" in action.lower():
        props.append({"name": "error_code", "type": "string", "description": "Machine-readable error code", "required": False})
        props.append({"name": "error_message", "type": "string", "description": "Human-readable error message", "required": False})
    if "click" in action.lower() or "cta" in action.lower():
        props.append({"name": "element_id", "type": "string", "description": "Frontend identifier for the clicked element", "required": False})
        props.append({"name": "page", "type": "string", "description": "Page or screen where the action occurred", "required": False})
    return props

def generate_tracking_plan(
    feature_name: str,
    feature_description: str,
    key_actions: List[str],
    platform: str = "web",
    funnel_stages: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Generate a tracking plan structure for a given feature.
    """
    if not funnel_stages:
        funnel_stages = ["view", "start", "complete"]

    events: List[Dict[str, Any]] = []

    # Core funnel events
    for stage in funnel_stages:
        events.append({
            "event_name": _event_name(feature_name, stage),
            "friendly_name": f"{feature_name} - {stage.capitalize()}",
            "description": f"Fired when a user {stage}s the {feature_name} feature.",
            "when_triggered": f"User {stage}s the {feature_name} flow.",
            "platform": platform,
            "properties": _default_properties(stage),
            "category": "funnel"
        })

    # Key action events
    for action in key_actions:
        if not action.strip():
            continue
        events.append({
            "event_name": _event_name(feature_name, action),
            "friendly_name": f"{feature_name} - {action.capitalize()}",
            "description": f"Fired when a user performs key action: {action}.",
            "when_triggered": f"User completes action: {action}.",
            "platform": platform,
            "properties": _default_properties(action),
            "category": "behavior"
        })

    taxonomy_issues = validate_taxonomy(events)

    tracking_plan = {
        "feature_name": feature_name,
        "feature_description": feature_description,
        "platform": platform,
        "events": events,
        "taxonomy_issues": taxonomy_issues,
    }
    return tracking_plan

def validate_taxonomy(events: List[Dict[str, Any]]) -> List[str]:
    """
    Simple checks for naming, required properties, and consistency.
    """
    issues = []
    seen_names = set()
    for ev in events:
        name = ev["event_name"]
        if name in seen_names:
            issues.append(f"Duplicate event name detected: {name}")
        seen_names.add(name)

        if not SNAKE_CASE_PATTERN.match(name):
            issues.append(f"Event name not snake_case: {name}")

        # Check required properties exist
        props = {p["name"]: p for p in ev.get("properties", [])}
        for required_prop in ["user_id", "workspace_id", "timestamp"]:
            if required_prop not in props:
                issues.append(f"Missing required property '{required_prop}' in event: {name}")
    return issues

def tracking_plan_to_markdown(plan: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Tracking Plan: {plan['feature_name']}")
    lines.append("")
    lines.append(plan.get("feature_description", ""))
    lines.append("")
    lines.append("## Events")
    lines.append("")
    for ev in plan["events"]:
        lines.append(f"### {ev['event_name']}")
        lines.append(f"- **Friendly name:** {ev['friendly_name']}")
        lines.append(f"- **Category:** {ev.get('category', 'n/a')}")
        lines.append(f"- **Platform:** {ev.get('platform', 'n/a')}")
        lines.append(f"- **When triggered:** {ev['when_triggered']}")
        lines.append(f"- **Description:** {ev['description']}")
        lines.append(f"- **Properties:**")
        for p in ev["properties"]:
            req = "required" if p["required"] else "optional"
            lines.append(f"  - `{p['name']}` ({p['type']}, {req}) — {p['description']}")
        lines.append("")
    if plan["taxonomy_issues"]:
        lines.append("## Taxonomy Warnings")
        lines.append("")
        for issue in plan["taxonomy_issues"]:
            lines.append(f"- {issue}")
    return "\n".join(lines)

def tracking_plan_to_dbt_yaml(plan: Dict[str, Any]) -> str:
    """
    Create a dbt-style YAML schema for the events.
    Each event is modeled as a separate model suggestion.
    """
    models = []
    for ev in plan["events"]:
        cols = []
        for p in ev["properties"]:
            cols.append({
                "name": p["name"],
                "description": p["description"],
                "tests": ["not_null"] if p["required"] else [],
            })
        models.append({
            "name": ev["event_name"],
            "description": ev["description"],
            "columns": cols,
        })
    schema = {"version": 2, "models": models}
    return yaml.safe_dump(schema, sort_keys=False)

def generate_sample_events(plan: Dict[str, Any], n: int = 10) -> list[dict]:
    """
    Generate synthetic sample events for testing or mocking.
    """
    events = []
    now = datetime.utcnow()
    for _ in range(n):
        ev_def = random.choice(plan["events"])
        ts = now - timedelta(minutes=random.randint(0, 60*24))
        payload = {"event_name": ev_def["event_name"]}
        for p in ev_def["properties"]:
            if p["name"] == "user_id":
                payload["user_id"] = f"user_{random.randint(1, 50)}"
            elif p["name"] == "workspace_id":
                payload["workspace_id"] = f"ws_{random.randint(1, 10)}"
            elif p["name"] == "timestamp":
                payload["timestamp"] = ts.isoformat() + "Z"
            elif p["name"] == "error_code":
                payload["error_code"] = random.choice(["", "E_TIMEOUT", "E_500"])
            elif p["name"] == "error_message":
                payload["error_message"] = random.choice(["", "Timeout", "Internal server error"])
            elif p["name"] == "element_id":
                payload["element_id"] = random.choice(["cta_primary", "secondary_button", "link_text"])
            elif p["name"] == "page":
                payload["page"] = random.choice(["settings", "dashboard", "feature_page"])
            else:
                payload[p["name"]] = None
        events.append(payload)
    return events
