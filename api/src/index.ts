import { Redis } from '@upstash/redis';
import express, { Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import jwt from 'jsonwebtoken';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

const redis = new Redis({
    url: process.env.REDIS_URL,
    token: process.env.REDIS_TOKEN || "",
});

app.use(cors());
app.use(express.json());

interface Task {
    id: number;
    title: string;
    completed: boolean;
    last_updated: number;
    next_timeout: number;
}

// Middleware to check for JWT token
const authenticateJWT = (req: Request, res: Response, next: NextFunction) => {
    const token = req.header('Authorization')?.split(' ')[1]; // Bearer <token>
    if (token) {
        jwt.verify(token, process.env.JWT_SECRET as string, (err: any, user: any) => {
            if (err) {
                return res.sendStatus(403);
            }
            next();
        });
    } else {
        res.sendStatus(401); // Unauthorized
    }
};

// Root endpoint
app.get('/', (req: Request, res: Response) => {
    res.send({ 'message': 'API /' });
});

// Login endpoint to authenticate and provide a JWT
app.post('/auth/login', async (req: Request, res: Response) => {
    const { username, password } = req.body;
    if (username === process.env.ADMIN_USERNAME && password === process.env.ADMIN_PASSWORD) {
        const token = jwt.sign({ username }, process.env.JWT_SECRET as string, { expiresIn: '8h' });
        return res.json({ token });
    }
    return res.sendStatus(403); // Forbidden
});

// Get all tasks (secured)
app.get('/tasks', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const taskKeys = await redis.keys('task:*');
        if (taskKeys.length === 0) {
            return res.json({ tasks: [] });
        }
        const taskValues = await redis.mget(taskKeys);
        const tasks = taskValues.map((task) => task ? task : {}).filter(Boolean);
        res.json({ tasks });
    } catch (error) {
        console.error('Error fetching tasks:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});

// Create a new task (secured)
app.post('/tasks', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const newTask: Task = req.body;
        newTask.id = Date.now();  // Generate a unique ID
        const taskKey = `task:${newTask.id}`;
        await redis.set(taskKey, JSON.stringify(newTask));
        res.status(201).json({ task: newTask });
    } catch (error) {
        console.error('Error creating task:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});

// Update a task (secured)
app.put('/tasks/:id', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const taskId = Number(req.params.id);
        const taskKey = `task:${taskId}`;
        const updatedTaskData = req.body;
        const taskData = await redis.get(taskKey);
        if (!taskData) {
            return res.status(404).json({ message: 'Task not found' });
        }
        const task: Task = taskData as Task;
        task.completed = updatedTaskData.completed;
        task.last_updated = updatedTaskData.last_updated;
        task.next_timeout = updatedTaskData.next_timeout;
        await redis.set(taskKey, JSON.stringify(task));
        res.status(200).json({ task });
    } catch (error) {
        console.error('Error updating task:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});

// Delete a task (secured)
app.delete('/tasks/:id', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const taskId = Number(req.params.id);
        const taskKey = `task:${taskId}`;
        const taskData = await redis.get(taskKey);
        if (!taskData) {
            return res.status(404).json({ message: 'Task not found' });
        }
        await redis.del(taskKey);
        res.status(204).send();
    } catch (error) {
        console.error('Error deleting task:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});

module.exports = app;