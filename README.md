# Todo Application

A full-stack Todo application with authentication and task management features.

## Architecture

- **Frontend**: Next.js React application deployed on Vercel
- **Backend**: FastAPI application deployed on Hugging Face Spaces
- **Database**: PostgreSQL (Neon)

## Deployment Instructions

### Backend Deployment (Hugging Face)

1. **Prepare Backend Repository**:
   - Push the `backend` folder to a GitHub repository
   - Make sure all necessary files are included:
     - `src/` directory with your FastAPI application
     - `requirements.txt` with dependencies
     - `Dockerfile` for containerization
     - `.env` with environment variables (add to Hugging Face Secrets)

2. **Create Hugging Face Space**:
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Create a new Space with Docker runtime
   - Connect to your GitHub repository
   - Configure the Space to run your FastAPI application

3. **Set Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: JWT secret key
   - `FRONTEND_URL`: URL of your Vercel frontend deployment

4. **Configure Dockerfile**:
   - The Dockerfile should expose port 8000
   - The application should run with uvicorn

### Frontend Deployment (Vercel)

1. **Prepare Frontend Repository**:
   - Push the `frontend` folder to a separate GitHub repository
   - Make sure `.env.local` contains:
     ```
     NEXT_PUBLIC_API_URL=https://your-hugging-face-space-username.hf.space
     ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your frontend repository
   - In the Vercel dashboard, set the environment variable:
     - Key: `NEXT_PUBLIC_API_URL`
     - Value: `https://your-hugging-face-space-username.hf.space` (your backend URL)

3. **Build Settings**:
   - Framework: Next.js (should be auto-detected)
   - Build command: `npm run build`
   - Install command: `npm install`

## Environment Variables

### Backend (Hugging Face)
- `DATABASE_URL`: PostgreSQL database connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `FRONTEND_URL`: URL of the frontend application (for CORS)

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL`: URL of the backend API

## CORS Configuration

The backend is configured to allow requests from the specified frontend URL. Make sure to update `FRONTEND_URL` in the backend environment variables after deploying the frontend.

## Health Check

The backend includes a health check endpoint at `/health` that returns `{"status": "healthy"}`.

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login a user
- `GET /auth/me` - Get current user info
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

### Tasks
- `GET /tasks` - Get all tasks for current user
- `POST /tasks` - Create a new task
- `GET /tasks/{id}` - Get a specific task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

## Troubleshooting

1. **CORS Issues**: Make sure `FRONTEND_URL` in the backend matches the deployed frontend URL exactly.

2. **Connection Issues**: Verify that the `NEXT_PUBLIC_API_URL` in the frontend points to the correct backend URL.

3. **Database Issues**: Ensure the `DATABASE_URL` is properly configured in the backend environment.

## Scaling

Both frontend and backend can scale independently. Monitor your usage and adjust resources as needed.

## Security

- Authentication tokens are securely stored in the frontend
- Passwords are hashed using bcrypt
- CORS is restricted to the frontend domain only
- Environment variables are kept secure