import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../../../lib/auth';

const prisma = new PrismaClient();

export default async function handler(req, res) {
  const decoded = authenticateToken(req);
  if (!decoded) {
    return res.status(401).json({ detail: 'Unauthorized' });
  }

  if (req.method === 'GET') {
    try {
      const tasks = await prisma.task.findMany({
        where: { user_id: decoded.sub },
        orderBy: { created_at: 'desc' }
      });

      res.status(200).json(tasks.map(task => ({
        ...task,
        tags: task.tags ? JSON.parse(task.tags) : []
      })));
    } catch (error) {
      console.error('Get tasks error:', error);
      res.status(500).json({ detail: 'Server error' });
    } finally {
      await prisma.$disconnect();
    }
  } else if (req.method === 'POST') {
    const { title, description, priority = 'Medium', tags = [] } = req.body;

    try {
      const task = await prisma.task.create({
        data: {
          title,
          description,
          priority,
          tags: JSON.stringify(tags),
          user_id: decoded.sub
        }
      });

      res.status(200).json({
        ...task,
        tags: tags
      });
    } catch (error) {
      console.error('Create task error:', error);
      res.status(500).json({ detail: 'Server error' });
    } finally {
      await prisma.$disconnect();
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}