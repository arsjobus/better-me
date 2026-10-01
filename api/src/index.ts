import { createClient, RedisClientType } from 'redis';
import express, { Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { jwtVerify, SignJWT } from 'jose';

dotenv.config();

const app = express();
const port = Number(process.env.PORT || 3000);

const redis: RedisClientType = createClient({
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    password: process.env.REDIS_TOKEN || undefined,
});

redis.on('error', (err) => console.error('Redis Client Error', err));

const getJwtSecret = () => {
    const secret = process.env.JWT_SECRET;
    if (!secret) {
        throw new Error('JWT_SECRET is required to sign or verify tokens');
    }
    return new TextEncoder().encode(secret);
};

app.use(cors());
app.use(express.json());

const startServer = async () => {
    await redis.connect();
    app.listen(port, () => {
        console.log(`API running on http://localhost:${port}`);
    });
};

startServer().catch((error) => {
    console.error('Failed to start API server:', error);
    process.exit(1);
});

interface Task {
    id: number;
    title: string;
    completed: boolean;
    last_updated: number;
    next_timeout: number;
}

// Middleware to check for JWT token
const authenticateJWT = async (req: Request, res: Response, next: NextFunction) => {
    const token = req.header('Authorization')?.split(' ')[1]; // Bearer <token>
    if (!token) {
        res.sendStatus(401); // Unauthorized
        return;
    }

    try {
        await jwtVerify(token, getJwtSecret());
        next();
    } catch {
        res.sendStatus(403);
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
        const token = await new SignJWT({ username })
            .setProtectedHeader({ alg: 'HS256' })
            .setIssuedAt()
            .setExpirationTime('8h')
            .sign(getJwtSecret());
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
        const taskValues = await redis.mGet(taskKeys);
        const tasks = taskValues
            .filter((task): task is string => typeof task === 'string')
            .map((task) => JSON.parse(task));
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
        const task = JSON.parse(taskData as string) as Task;
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