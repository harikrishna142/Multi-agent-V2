# Quick Setup Guide - Multi-Agentic Framework

## 🚀 **Get Started in 5 Minutes**

### **Step 1: Environment Setup**
```bash
# Create a .env file with your OpenAI API key
cp env_example.txt .env
```

Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
MODEL_NAME=gpt-4
TEMPERATURE=0.7
MAX_ITERATIONS=3
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Test the Framework**
```bash
python test_basic.py
```

You should see: `🎉 All tests passed! Framework is ready for use.`

### **Step 4: Launch the Application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🎯 **How to Use**

1. **Enter Requirements**: Type your project requirements in natural language
2. **Configure Options**: Set max iterations, temperature, and which agents to use
3. **Start Processing**: Click "🚀 Start Multi-Agent Processing"
4. **Download Results**: Get the complete project as a ZIP file

## 📝 **Example Requirements**

Try these example requirements:

- "Create a simple calculator application that can perform basic arithmetic operations"
- "Build a web-based todo list application with user authentication"
- "Develop a weather app that fetches data from a weather API"
- "Create a file management system with CRUD operations"

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"No module named 'autogen'"**
   ```bash
   pip install autogen
   ```

2. **"OpenAI API key not found"**
   - Make sure you have a `.env` file with your API key
   - Get an API key from: https://platform.openai.com/api-keys

3. **"Framework import failed"**
   ```bash
   python test_basic.py
   ```
   This will show which specific import is failing.

### **Getting Help:**
- Check the logs in `multi_agent_framework.log`
- Run `python test_basic.py` to verify setup
- Ensure all dependencies are installed: `pip list`

## 🎉 **You're Ready!**

The framework is now ready to generate complete software projects from your natural language requirements. Each project will include:

- ✅ Functional Python code
- ✅ Comprehensive documentation
- ✅ Unit tests
- ✅ Deployment configurations
- ✅ Web UI (if requested)
- ✅ Complete project structure

Happy coding! 🚀 