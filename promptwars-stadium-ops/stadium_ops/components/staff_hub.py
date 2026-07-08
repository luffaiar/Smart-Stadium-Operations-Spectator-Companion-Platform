"""Staff operations control room UI component.

This module renders live crowd occupancy heatmaps, transit boards, and volunteers
dispatch consoles, coordinating incident logs and volunteer assignments.
"""

import time
import streamlit as st
from stadium_ops.core.security import (
    sanitize_input,
    detect_prompt_injection,
    enforce_length_limit,
    is_rate_limited,
    log_security_violation
)
from stadium_ops.core.exceptions import SecurityValidationError
from stadium_ops.services.crowd_management import CrowdManagementService
from stadium_ops.services.transport_service import TransportService


def render_staff_hub(selected_stadium: str) -> None:
    """Renders the smart control room dashboard for stadium staff.

    Args:
        selected_stadium: The name of the currently selected venue.
    """
    st.header("🏟️ Stadium Live Control Room")
    st.subheader(f"Current Operations Dashboard: {selected_stadium}")
    
    # 1. Live Crowd Densities (Simulated)
    st.write("### 👥 Simulated Live Crowd Density")
    sectors = CrowdManagementService.get_simulated_sectors(selected_stadium)
    
    cols = st.columns(len(sectors))
    for i, sector in enumerate(sectors):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border-left: 5px solid {sector['color']}; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 120px;">
                    <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{sector['name']}</div>
                    <div style="font-size: 24px; font-weight: 900; color: #0f172a; margin-top: 5px;">{sector['density']}%</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">{sector['description']}</div>
                    <span style="display: inline-block; background-color: {sector['color']}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-top: 8px;">{sector['status']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # 2. Automated Crowd Redistribution Action Plan
    st.write("### 📈 Operations Intelligence Advice")
    recs = CrowdManagementService.get_crowd_recommendations(sectors)
    for rec in recs:
        st.markdown(rec)
        
    st.markdown("---")
    
    # 3. Real-Time Transportation Monitor
    st.write("### 🚇 Real-Time Match-Day Transportation Monitor")
    transit_routes = TransportService.get_transit_status(selected_stadium)
    cols_transit = st.columns(len(transit_routes))
    for idx, route in enumerate(transit_routes):
        with cols_transit[idx]:
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border-top: 4px solid {route['color']}; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-height: 110px;">
                    <div style="font-size: 16px; font-weight: 700; color: #0f172a;">{route['icon']} {route['route']}</div>
                    <div style="font-size: 13px; color: #475569; margin-top: 3px;">Frequency: {route['frequency']}</div>
                    <span style="display: inline-block; color: {route['color']}; font-weight: bold; font-size: 13px; margin-top: 6px;">Status: {route['status']}</span>
                    {f"<br><span style='font-size:11px; color:#ef4444;'>Delay: {route['delay']}</span>" if route['status'] in ['Delayed', 'Congested'] else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.markdown("---")
    
    # 4. GenAI Incident Dispatcher
    st.write("### 🚨 GenAI Incident Dispatcher")
    st.write("Input incident notifications reported by field staff or cameras to classify and create actionable response procedures.")
    
    incident_input = st.text_area(
        "Incident details (e.g. 'A spectator fainted near Sector 102 concession stands')",
        placeholder="Type incident report here...",
        height=100
    )
    
    if st.button("Log & Classify Incident"):
        # 1. Rate Limiter Validation
        if is_rate_limited(st.session_state.request_timestamps, limit=6, period=60.0):
            st.error("⚠️ Rate Limit Triggered: You are submitting requests too quickly. Please wait a moment.")
            log_security_violation("RATE_LIMIT_EXCEEDED", "Incident log submission spamming", "StaffSession")
        else:
            try:
                # 2. Input Size Guards (300 character cap)
                enforce_length_limit(incident_input, max_len=300)
                
                # 3. HTML Sanitization
                sanitized_report = sanitize_input(incident_input)
                
                if not sanitized_report:
                    st.warning("Please type a description of the incident before submission.")
                # 4. Prompt Injection Blockers
                elif detect_prompt_injection(sanitized_report, user_id="StaffSession"):
                    st.error("🚨 Security Alert: Prompt injection patterns detected! Operation aborted.")
                else:
                    # Update rate limit timestamps
                    st.session_state.request_timestamps.append(time.time())
                    
                    with st.spinner("GenAI analyzing severity and building response checklists..."):
                        analysis = CrowdManagementService.analyze_and_dispatch_incident(sanitized_report)
                        
                        if analysis:
                            # 5. Smart Volunteer Proximity Dispatch Allocation
                            category = analysis.get("category", "General")
                            role_map = {
                                "Medical": "Medical Assistant",
                                "Security": "Venue Security Assistant",
                                "Facilities / Maintenance": "Facilities support"
                            }
                            target_role = role_map.get(category, "General Support")
                            
                            # Retrieve list of available matching volunteers
                            candidates = [v for v in st.session_state.volunteer_roster if v["role"] == target_role and v["status"] == "Available"]
                            if not candidates:
                                candidates = [v for v in st.session_state.volunteer_roster if v["role"] in ["General Support", "Navigational Guide"] and v["status"] == "Available"]
                                
                            matched_volunteer = None
                            if candidates:
                                # Prioritize exact sector matches in report text
                                for c in candidates:
                                    if c["sector"].lower() in sanitized_report.lower():
                                        matched_volunteer = c
                                        break
                                if not matched_volunteer:
                                    matched_volunteer = candidates[0]
                                    
                            if matched_volunteer:
                                matched_volunteer["status"] = "Dispatched"
                                volunteer_name = f"{matched_volunteer['name']} ({matched_volunteer['role']}) - Sector: {matched_volunteer['sector']}"
                            else:
                                volunteer_name = "None Available (Escalating to Operations Command)"
                                
                            st.session_state.incidents.insert(0, {
                                "report": sanitized_report,
                                "analysis": analysis,
                                "volunteer": volunteer_name
                            })
                            st.success("Incident logged successfully!")
                        else:
                            st.error("Could not process the incident.")
            except SecurityValidationError as e:
                st.error(f"⚠️ Security Validation Failed: {e}")
                log_security_violation("INPUT_SIZE_VIOLATION", incident_input, "StaffSession")
                    
    # Render logged incidents (Uses secure native Streamlit info message box, eliminating XSS risks)
    if st.session_state.incidents:
        st.write("#### Active Incidents Queue")
        for idx, inc in enumerate(st.session_state.incidents):
            report_text = inc["report"]
            analysis = inc["analysis"]
            volunteer = inc.get("volunteer", "None Assigned")
            severity = analysis.get("severity", "Low")
            category = analysis.get("category", "General")
            dept = analysis.get("department", "Rescue Squad")
            checklist = analysis.get("checklist", [])
            
            with st.expander(f"⚠️ {category} Alert ({severity} Urgency) - {report_text[:40]}...", expanded=True):
                st.info(
                    f"📝 **Original Report:** {report_text}  \n"
                    f"🏢 **Assigned Responder Unit:** {dept}  \n"
                    f"🎯 **Dispatched Volunteer:** {volunteer}"
                )
                
                st.write("**Dispatched Actions Checklist:**")
                for step in checklist:
                    st.checkbox(step, key=f"step_{idx}_{step[:25]}")
