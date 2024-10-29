# User Validation Microservice

This microservice is part of the Gamezon ecosystem and is used for user registration, login, and validation. It manages user authentication through JWT (JSON Web Tokens) to ensure secure access.

## Running the Application

1. **Set up a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    ```bash
    uvicorn main:app --host 127.0.0.1 --port 8001 --reload
    ```

4. **Access the API Documentation**:
   Navigate to `http://127.0.0.1:8001/docs` in your web browser to view and interact with the API endpoints.