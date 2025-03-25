import streamlit as st
import pandas as pd
from pdf_processor import process_pdf_file, process_image_file
from llm_analyzer import analyze_results
from rag_chatbot import get_chatbot_response
from medical_history_viz import show_medical_history_visualization
from export_handler import export_to_csv, export_to_json, export_to_html
from whatsapp_handler import send_whatsapp_message
import os

def main():
    st.set_page_config(page_title="Hemoglobinopathy Analysis", layout="wide")

    st.title("Hemoglobinopathy Analysis System")

    # Initialize session state
    if 'registered_patients' not in st.session_state:
        st.session_state.registered_patients = set()
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {
            'RBC': None,
            'HGB': None,
            'MCV': None,
            'MCH': None,
            'MCHC': None,
            'RDW': None,
            'F_concentration': None,
            'A2_concentration': None,
            'Ao_peak': None,
            'S_peak': None
        }
    if 'current_assessment' not in st.session_state:
        st.session_state.current_assessment = None
    if 'pathologist_notes' not in st.session_state:
        st.session_state.pathologist_notes = None

    # Create tabs for different sections
    tabs = st.tabs(["Analysis", "Patient Management", "Medical History", "Chatbot"])

    # Patient Management Tab
    with tabs[1]:
        st.header("Patient WhatsApp Registration")

        # Add Twilio Sandbox Instructions
        st.info("""
        **Important: Before registering, connect to our WhatsApp service:**
        1. Save our WhatsApp number: {}
        2. Send "join <sandbox-code>" to this number
        3. Wait for confirmation before registering

        This is required for the Twilio WhatsApp Sandbox.
        """.format(os.getenv('TWILIO_PHONE_NUMBER', 'Number not configured')))

        # Patient registration form
        with st.form("patient_registration"):
            patient_number = st.text_input(
                "Patient's WhatsApp Number (e.g., +234XXXXXXXXXX)",
                help="Enter the full number including country code (e.g., +234...)"
            )
            st.caption("Make sure you've completed the sandbox connection steps above.")
            submit_registration = st.form_submit_button("Register Patient")

            if submit_registration and patient_number:
                try:
                    welcome_message = """Welcome to the Hemoglobinopathy Analysis System!

You can:
1. Ask questions about hemoglobinopathies
2. Contact your doctor by starting your message with 'doctor:'
3. Get immediate AI assistance for medical queries
4. Access your test results and medical history

Reply with any question to get started!

For technical support, please contact our help desk."""

                    if send_whatsapp_message(patient_number, welcome_message):
                        st.session_state.registered_patients.add(patient_number)
                        st.success(f"Successfully registered patient and sent welcome message to: {patient_number}")
                    else:
                        st.error("""
                        Failed to send welcome message. Please ensure:
                        1. The phone number format is correct (e.g., +234XXXXXXXXXX)
                        2. You've joined our WhatsApp sandbox (see instructions above)
                        3. Your number matches the one you used to join the sandbox
                        """)
                except Exception as e:
                    st.error(f"Error registering patient: {str(e)}")
            elif submit_registration:
                st.warning("Please enter a valid WhatsApp number")

        # Display registered patients
        if st.session_state.registered_patients:
            st.subheader("Registered Patients")
            for number in st.session_state.registered_patients:
                st.code(number)

        # WhatsApp Integration Info
        st.header("WhatsApp Integration")
        st.info("""
        Patients can interact with the chatbot and doctor via WhatsApp:
        1. Send a message to start chatting with the AI
        2. Start message with 'doctor:' to contact the doctor directly
        3. The doctor can respond to specific patients
        """)

        # Display WhatsApp number
        st.subheader("System WhatsApp Number")
        st.code(f"{os.getenv('TWILIO_PHONE_NUMBER')}")

    # Analysis Tab
    with tabs[0]:
        # File upload section
        st.header("Upload Medical Report")
        uploaded_file = st.file_uploader("Choose a PDF or image file", type=['pdf', 'png', 'jpg', 'jpeg'])

        if uploaded_file:
            try:
                # Process the uploaded file
                if uploaded_file.type == "application/pdf":
                    results = process_pdf_file(uploaded_file)
                else:
                    results = process_image_file(uploaded_file)

                # Update session state with extracted values
                st.session_state.parameters.update(results)

            except Exception as e:
                st.warning(f"Could not automatically extract all values. You can enter them manually below.")

        # Parameters input section
        st.header("Blood Test Parameters")
        st.info("You can manually enter or adjust these values if needed")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.parameters['RBC'] = st.number_input(
                "RBC", 
                value=float(st.session_state.parameters['RBC']) if st.session_state.parameters['RBC'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['HGB'] = st.number_input(
                "HGB",
                value=float(st.session_state.parameters['HGB']) if st.session_state.parameters['HGB'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['MCV'] = st.number_input(
                "MCV",
                value=float(st.session_state.parameters['MCV']) if st.session_state.parameters['MCV'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['MCH'] = st.number_input(
                "MCH",
                value=float(st.session_state.parameters['MCH']) if st.session_state.parameters['MCH'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['MCHC'] = st.number_input(
                "MCHC",
                value=float(st.session_state.parameters['MCHC']) if st.session_state.parameters['MCHC'] is not None else 0.0,
                format="%.2f"
            )

        with col2:
            st.session_state.parameters['RDW'] = st.number_input(
                "RDW",
                value=float(st.session_state.parameters['RDW']) if st.session_state.parameters['RDW'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['F_concentration'] = st.number_input(
                "F Concentration",
                value=float(st.session_state.parameters['F_concentration']) if st.session_state.parameters['F_concentration'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['A2_concentration'] = st.number_input(
                "A2 Concentration",
                value=float(st.session_state.parameters['A2_concentration']) if st.session_state.parameters['A2_concentration'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['Ao_peak'] = st.number_input(
                "Ao Peak",
                value=float(st.session_state.parameters['Ao_peak']) if st.session_state.parameters['Ao_peak'] is not None else 0.0,
                format="%.2f"
            )
            st.session_state.parameters['S_peak'] = st.number_input(
                "S Peak",
                value=float(st.session_state.parameters['S_peak']) if st.session_state.parameters['S_peak'] is not None else 0.0,
                format="%.2f"
            )

        # Analysis button
        if st.button("Analyze Results"):
            try:
                # Get system assessment using current parameters
                assessment = analyze_results(st.session_state.parameters)
                st.session_state.current_assessment = assessment

                st.header("Analysis")
                col3, col4 = st.columns(2)

                with col3:
                    st.subheader("System Assessment")
                    st.write(assessment['system_assessment'])

                with col4:
                    st.subheader("Pathologist Review")
                    st.session_state.pathologist_notes = st.text_area(
                        "Enter pathologist notes",
                        value=st.session_state.pathologist_notes if st.session_state.pathologist_notes else "",
                        height=150
                    )
                    if st.button("Save Pathologist Review"):
                        st.success("Pathologist review saved successfully")

                # Export section
                st.header("Export Results")
                export_col1, export_col2, export_col3 = st.columns(3)

                with export_col1:
                    if st.button("Export as CSV"):
                        try:
                            csv_data = export_to_csv(
                                st.session_state.parameters,
                                st.session_state.current_assessment,
                                st.session_state.pathologist_notes
                            )
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="analysis_results.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.error(f"Error exporting to CSV: {str(e)}")

                with export_col2:
                    if st.button("Export as JSON"):
                        try:
                            json_data = export_to_json(
                                st.session_state.parameters,
                                st.session_state.current_assessment,
                                pathologist_notes=st.session_state.pathologist_notes
                            )
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name="analysis_results.json",
                                mime="application/json"
                            )
                        except Exception as e:
                            st.error(f"Error exporting to JSON: {str(e)}")

                with export_col3:
                    if st.button("Export as HTML Report"):
                        try:
                            html_data = export_to_html(
                                st.session_state.parameters,
                                st.session_state.current_assessment,
                                pathologist_notes=st.session_state.pathologist_notes
                            )
                            st.download_button(
                                label="Download HTML Report",
                                data=html_data,
                                file_name="analysis_report.html",
                                mime="text/html"
                            )
                        except Exception as e:
                            st.error(f"Error exporting to HTML: {str(e)}")

            except Exception as e:
                st.error(f"Error in analysis: {str(e)}")

    # Medical History Tab
    with tabs[2]:
        show_medical_history_visualization()

    # Chatbot Tab
    with tabs[3]:
        st.header("Hemoglobinopathy Information Chatbot")
        st.write("Ask questions about hemoglobinopathies and get informed answers.")

        user_question = st.text_input("Ask a question:")
        if user_question:
            with st.spinner("Getting answer..."):
                try:
                    response = get_chatbot_response(user_question)
                    st.write("Answer:", response)
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")

if __name__ == "__main__":
    main()