import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    raise Exception(f"Failed to initialize OpenAI client: {str(e)}")

def analyze_results(parameters):
    """
    Analyze blood test results and provide assessment for potential hemoglobinopathies.
    """
    try:
        # Prepare the prompt with medical parameters
        prompt = f"""
        Analyze the following blood test results and provide an assessment for potential hemoglobinopathies:

        RBC: {parameters.get('RBC', 'N/A')}
        HGB: {parameters.get('HGB', 'N/A')}
        MCV: {parameters.get('MCV', 'N/A')}
        MCH: {parameters.get('MCH', 'N/A')}
        MCHC: {parameters.get('MCHC', 'N/A')}
        RDW: {parameters.get('RDW', 'N/A')}
        F Concentration: {parameters.get('F_concentration', 'N/A')}
        A2 Concentration: {parameters.get('A2_concentration', 'N/A')}
        Ao Peak: {parameters.get('Ao_peak', 'N/A')}
        S Peak: {parameters.get('S_peak', 'N/A')}

        Classify the results into one of the following categories:
        1. Sickle Cell Disease
        2. Sickle Cell Trait
        3. Alpha Thalassemia Trait
        4. Beta Thalassemia Trait
        5. Normal Findings
        6. For Further Review by Pathologist

        Provide detailed reasoning for the classification.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical expert specializing in hemoglobinopathy analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return {
            "system_assessment": response.choices[0].message.content
        }
    except Exception as e:
        print(f"Error in analyze_results: {str(e)}")
        raise Exception(f"Error in LLM analysis: {str(e)}")

# Export the function
__all__ = ['analyze_results']