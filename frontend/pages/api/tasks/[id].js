import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../../../lib/auth';

const prisma = new PrismaClient();

export default async function handler(req, res) {
  const decoded = authenticateToken(req);
  if (!decoded) {
    return res.status(401).json({ detail: 'Unauthorized' });
  }

  // Extract task ID from the URL
  const taskId = parseInt(req.query.id);

  if (req.method === 'GET') {
    try {
      const task = await prisma.task.findFirst({
        where: {
          id: taskId,
          user_id: decoded.sub
        }
      });

      if (!task) {
        return res.status(404).json({ detail: 'Task not found' });
      }

      res.status(200).json({
        ...task,
        tags: task.tags ? JSON.parse(task.tags) : []
      });
    } catch (error) {
      console.error('Get task error:', error);
      res.status(500).json({ detail: 'Server error' });
    } finally {
      await prisma.$disconnect();
    }
  } else if (req.method === 'PUT') {
    const { title, description, completed, priority, tags } = req.body;

    try {
      const task = await prisma.task.findFirst({
        where: {
          id: taskId,
          user_id: decoded.sub
        }
      });

      if (!task) {
        return res.status(404).json({ detail: 'Task not found' });
      }

      const updatedTask = await prisma.task.update({
        where: { id: taskId },
        data: {
          ...(title !== undefined && { title }),
          ...(description !== undefined && { description }),
          ...(completed !== undefined && { completed }),
          ...(priority !== undefined && { priority }),
          ...(tags !== undefined && { tags: JSON.stringify(tags) })
        }
      });

      res.status(200).json({
        ...updatedTask,
        tags: tags || (updatedTask.tags ? JSON.parse(updatedTask.tags) : [])
      });
    } catch (error) {
      console.error('Update task error:', error);
      res.status(500).json({ detail: 'Server error' });
    } finally {
      await prisma.$disconnect();
    }
  } else if (req.method === 'DELETE') {
    try {
      const task = await prisma.task.findFirst({
        where: {
          id: taskId,
          user_id: decoded.sub
        }
      });

      if (!task) {
        return res.status(404).json({ detail: 'Task not found' });
      }

      await prisma.task.delete({
        where: { id: taskId }
      });

      res.status(200).json({ message: 'Task deleted successfully' });
    } catch (error) {
      console.error('Delete task error:', error);
      res.status(500).json({ detail: 'Server error' });
    } finally {
      await prisma.$disconnect();
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}