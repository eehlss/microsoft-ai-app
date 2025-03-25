# Hemoglobinopathy Analysis Platform

A comprehensive medical analysis platform for hemoglobinopathy detection that leverages advanced technologies for patient care and medical insights.

## Features

- **PDF/Image Analysis**: Extract medical data from documents
- **LLM-Powered Analysis**: Advanced analysis using GPT-4o
- **RAG-based Chatbot**: Intelligent medical information assistant
- **WhatsApp Integration**: Patient communication system
- **Interactive Visualizations**: Medical history tracking and analysis
- **Multi-format Export**: CSV, JSON, and HTML report generation

## Deployment Options

### 1. Replit Deployment (Recommended)

1. Fork this repository to your Replit account
2. Set up the following secrets in your Replit environment:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `TWILIO_ACCOUNT_SID`: Your Twilio account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio auth token
   - `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number
3. Click the "Deploy" button in your Replit workspace

### 2. Azure Container Apps Deployment

1. Install Azure CLI and login:
   ```bash
   az login
   ```

2. Create Azure Container Registry:
   ```bash
   az acr create --name <registry-name> --resource-group <resource-group> --sku Basic
   az acr login --name <registry-name>
   ```

3. Build and push the Docker image:
   ```bash
   docker build -t hemoglobinopathy-analysis .
   docker tag hemoglobinopathy-analysis <registry-name>.azurecr.io/hemoglobinopathy-analysis
   docker push <registry-name>.azurecr.io/hemoglobinopathy-analysis
   ```

4. Create Azure Container App:
   ```bash
   az containerapp create \
     --name hemoglobinopathy-analysis \
     --resource-group <resource-group> \
     --image <registry-name>.azurecr.io/hemoglobinopathy-analysis \
     --target-port 5000 \
     --ingress external \
     --env-vars \
       OPENAI_API_KEY=<your-key> \
       TWILIO_ACCOUNT_SID=<your-sid> \
       TWILIO_AUTH_TOKEN=<your-token> \
       TWILIO_PHONE_NUMBER=<your-number> \
       DEPLOY_WHATSAPP_SERVER=true
   ```

5. Configure WhatsApp Webhook:
   - Get your Azure Container App URL from the Azure portal
   - In Twilio Console, set the WhatsApp webhook URL to:
     `https://<your-app-url>/whatsapp`

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for LLM analysis
- `TWILIO_ACCOUNT_SID`: Twilio account SID for WhatsApp integration
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_PHONE_NUMBER`: Twilio WhatsApp number

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/eehlss/microsoft-ai-app.git
   cd microsoft-ai-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.