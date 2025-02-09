# Backend

## Overview
This backend service is part of the Git Sample project. It provides various endpoints to support the application's functionality.

## Endpoint

### POST /chat/
This endpoint allows users to send messages to the chat service.

#### Request
- **URL:** `/chat/`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body:**
    ```json
    {
        "question": "Your query here"
    }
    ```

#### Response
- **Status:** `200 OK`
- **Body:**
    ```json
    {
        "response": "Response message here"
    }
    ```

## Setup
To set up the backend, follow these steps:

1. Clone the repository:
     ```sh
     git clone <repository-url>
     ```

2. Navigate to the backend directory:
     ```sh
     cd backend
     ```

3. Install dependencies:
     ```sh
     pip install -r requirements.txt
     ```

4. Run the server:
     ```sh
     fastapi dev api.py
     ```

## License
This project is licensed under the MIT License.