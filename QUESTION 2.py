import streamlit as st
import operator

# ==========================================
# 1. RULE ENGINE (Adapted from rbs_streamlit.py)
# ==========================================

# Define operators
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

# Define the Rules based on Table 1
AC_RULES = [
    {
        "name": "Windows open -> turn AC off",
        "priority": 100,
        "conditions": [
            ["windows_open", "==", True]
        ],
        "action": {"AC Mode": "OFF", "Fan Speed": "LOW", "Setpoint": "-", "Reason": "Windows are open"}
    },
    {
        "name": "No one home -> eco mode",
        "priority": 90,
        "conditions": [
            ["occupancy", "==", "EMPTY"],
            ["temperature", ">=", 24]
        ],
        "action": {"AC Mode": "ECO", "Fan Speed": "LOW", "Setpoint": "27°C", "Reason": "Home empty; save energy"}
    },
    {
        "name": "Too cold -> turn off",
        "priority": 85,
        "conditions": [
            ["temperature", "<=", 22]
        ],
        "action": {"AC Mode": "OFF", "Fan Speed": "LOW", "Setpoint": "-", "Reason": "Already cold"}
    },
    {
        "name": "Hot & humid (occupied) -> cool strong",
        "priority": 80,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 30],
            ["humidity", ">=", 70]
        ],
        "action": {"AC Mode": "COOL", "Fan Speed": "HIGH", "Setpoint": "23°C", "Reason": "Hot and humid"}
    },
    {
        "name": "Night (occupied) -> sleep mode",
        "priority": 75,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["time_of_day", "==", "NIGHT"],
            ["temperature", ">=", 26]
        ],
        "action": {"AC Mode": "SLEEP", "Fan Speed": "LOW", "Setpoint": "26°C", "Reason": "Night comfort"}
    },
    {
        "name": "Hot (occupied) -> cool",
        "priority": 70,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 28]
        ],
        "action": {"AC Mode": "COOL", "Fan Speed": "MEDIUM", "Setpoint": "24°C", "Reason": "Temperature high"}
    },
    {
        "name": "Slightly warm (occupied) -> gentle cool",
        "priority": 60,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 26],
            ["temperature", "<", 28]
        ],
        "action": {"AC Mode": "COOL", "Fan Speed": "LOW", "Setpoint": "25°C", "Reason": "Slightly warm"}
    }
]

def evaluate_condition(facts, cond):
    """Evaluates a single condition like ['temperature', '>=', 30]"""
    field, op_str, value = cond
    fact_val = facts.get(field)
    
    # If fact is missing, assume False
    if fact_val is None:
        return False
        
    op_func = OPS.get(op_str)
    if op_func:
        return op_func(fact_val, value)
    return False

def run_rules(facts, rules):
    """Finds the highest priority rule that matches the facts."""
    # Sort rules by priority (High to Low)
    sorted_rules = sorted(rules, key=lambda r: r['priority'], reverse=True)
    
    triggered_rules = []
    
    for rule in sorted_rules:
        conditions = rule['conditions']
        # Check if ALL conditions in this rule are true
        if all(evaluate_condition(facts, c) for c in conditions):
            triggered_rules.append(rule)
            
    # Return the highest priority match (first in list)
    if triggered_rules:
        return triggered_rules[0], triggered_rules
    return None, []

# ==========================================
# 2. STREAMLIT INTERFACE
# ==========================================
st.title("❄️ Smart Home AC Controller")
st.markdown("### Question 2: Rule-Based System")

# -- Input Section --
st.sidebar.header("Home Conditions")
temp = st.sidebar.number_input("Temperature (°C)", min_value=16, max_value=40, value=25)
humidity = st.sidebar.slider("Humidity (%)", 0, 100, 50)
occupancy = st.sidebar.selectbox("Occupancy", ["OCCUPIED", "EMPTY"])
time_of_day = st.sidebar.selectbox("Time of Day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"])
windows_open = st.sidebar.checkbox("Windows Open?", value=False)

# Collect Facts
facts = {
    "temperature": temp,
    "humidity": humidity,
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open
}

# Display Facts
col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Status")
    st.json(facts)

# -- Run Engine --
best_rule, all_matches = run_rules(facts, AC_RULES)

# -- Display Output --
with col2:
    st.subheader("Decision")
    if best_rule:
        action = best_rule['action']
        st.success(f"**Action:** {action['AC Mode']}")
        st.write(f"**Fan Speed:** {action['Fan Speed']}")
        st.write(f"**Setpoint:** {action['Setpoint']}")
        st.write(f"**Reason:** {action['Reason']}")
        st.info(f"**Rule Triggered:** {best_rule['name']} (Priority: {best_rule['priority']})")
    else:
        st.warning("No specific rule matched. Maintaining previous state.")