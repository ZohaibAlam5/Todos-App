import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../../../lib/auth';

const prisma = new PrismaClient();

export default async function handler(req, res) {
  const decoded = authenticateToken(req);
  if (!decoded) {
    return res.status(401).json({ detail: 'Unauthorized' });
  }

  try {
    const user = await prisma.user.findUnique({
      where: { id: decoded.sub }
    });

    if (!user) {
      return res.status(404).json({ detail: 'User not found' });
    }

    res.status(200).json({
      id: user.id,
      email: user.email,
      created_at: user.created_at,
      updated_at: user.updated_at
    });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ detail: 'Server error' });
  } finally {
    await prisma.$disconnect();
  }
}