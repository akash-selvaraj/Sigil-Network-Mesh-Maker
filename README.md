
---

# Sigil - Mobile Network Hotspot Detection During Floods
![Logo](https://github.com/user-attachments/assets/d404aa8b-364a-4a8a-8ec9-2b4f42291769)

This project, **Sigil**, is designed to help identify optimal mobile network hotspots in the event of floods. It uses Reinforcement Learning (RL) to determine areas with better mobile data speeds, allowing users to find efficient mobile networks quickly during emergencies.
![sigil](https://github.com/user-attachments/assets/5dc7e6f4-fe36-4283-a38f-ead010a58118)

This project, **Sigil**, is designed to help identify optimal mobile network hotspots in the event of floods. It uses Reinforcement Learning (RL) to determine areas with better mobile data speeds, allowing users to find efficient mobile networks quickly during emergencies.

## Project Structure

- **Frontend**: Built using Next.js, the frontend displays results related to mobile data speeds and network hotspots.
- **Backend**: The backend is a Python-based application (`app.py`), which utilizes RL algorithms to analyze mobile network speed and availability.

## Getting Started

### 1. Backend Setup

Before starting the frontend, you need to set up the backend Python server.

1. Navigate to the backend folder:

   ```
   cd backend
   ```

2. Create a virtual environment:

   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. Install the necessary dependencies from `requirements.txt`:

   ```
   pip install -r requirements.txt
   ```

5. Run the backend server:

   ```
   python app.py
   ```

### 2. Frontend Setup

Once the backend is running, proceed to set up the frontend.

1. Navigate to the Next.js project folder:

   ```
   cd frontend
   ```

2. Install dependencies:

   ```
   npm install
   # or
   yarn install
   # or
   pnpm install
   # or
   bun install
   ```

3. Run the development server:

   ```
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

4. Open `http://localhost:3000` with your browser to see the frontend connected to the backend.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

### Description

**Sigil** is intended to be used during floods, where mobile network stability is crucial. Using Reinforcement Learning, the system analyzes mobile data speeds across different areas and suggests the best locations for optimal network access. This information is presented to users through a responsive Next.js frontend, making it accessible and easy to use during emergencies.

### Resources

- Next.js Documentation - learn about Next.js features and API.
- Learn Next.js - an interactive Next.js tutorial.
- Vercel Deployment - Deploy your app with ease using Vercel.

---
