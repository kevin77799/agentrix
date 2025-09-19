# AgentriX Project

## Overview
AgentriX is a full-stack application that consists of a backend built with Python and a frontend developed using React. The application features a Streamlit dashboard for data visualization and interaction.

## Project Structure
```
agentrix
├── backend
│   ├── .venv                # Virtual environment for the backend
│   ├── dashboard.py         # Entry point for the Streamlit dashboard
│   ├── requirements.txt      # Python dependencies for the backend
│   └── src
│       └── app.py           # Main application logic for the backend
├── frontend
│   ├── src
│   │   └── index.tsx        # Entry point for the frontend application
│   ├── package.json         # Configuration file for npm
│   └── tsconfig.json        # TypeScript configuration file
├── start-all.bat           # Batch file to start all servers
└── README.md                # Project documentation
```

## Setup Instructions

### Backend
1. Navigate to the `backend` directory:
   ```
   cd backend
   ```
2. Create a virtual environment (if not already created):
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```
4. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

### Frontend
1. Navigate to the `frontend` directory:
   ```
   cd frontend
   ```
2. Install the necessary npm packages:
   ```
   npm install
   ```

## Running the Application
To start the application, run the `start-all.bat` file. This will activate the backend virtual environment and launch both the Streamlit dashboard and the frontend server in separate command windows.

## Usage
- Access the Streamlit dashboard at `http://localhost:8501`.
- Access the frontend application at `http://localhost:3000`.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License.