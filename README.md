# Data Report Analyzer

An AI-powered tool for analyzing data reports using OpenAI's GPT-4 and Perplexity's DeepSeek models.

## Features

- Upload and analyze CSV data files
- Process text appendices
- Generate AI-powered insights
- Custom query functionality with history
- Support for multiple AI models (GPT-4, GPT-4 Turbo, DeepSeek R1)
- Secure API key input through the UI

## Setup

### Option 1: Local Setup

1. Clone the repository:
```bash
git clone https://github.com/ginug/Datasampublic.git
cd Datasampublic
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run Datasam.py
```

### Option 2: Docker Setup

1. Clone the repository:
```bash
git clone https://github.com/ginug/Datasampublic.git
cd Datasampublic
```

2. Build and run using Docker Compose:
```bash
docker-compose up --build
```

Or using Docker directly:
```bash
docker build -t datasam .
docker run -p 8501:8501 datasam
```

The application will be available at http://localhost:8501

## Usage

1. Upload your CSV data file
2. Upload your text appendix file
3. Select an AI model from the sidebar
4. Enter your API key(s) in the sidebar:
   - OpenAI API key for GPT-4 and GPT-4 Turbo
   - Perplexity API key for DeepSeek R1
5. Click "Run Analysis" for automated insights
6. Use the custom query section for specific questions

## Development

### Docker Development

1. Start the development environment:
```bash
docker-compose up --build
```

2. The application will automatically reload when you make changes to the code.

3. To stop the application:
```bash
docker-compose down
```

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run Datasam.py
```

## Deployment

The application is ready to be deployed to platforms like Heroku or Streamlit Cloud.

### Heroku Deployment

1. Install Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Deploy:
```bash
git push heroku main
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy from your GitHub repository

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) 
