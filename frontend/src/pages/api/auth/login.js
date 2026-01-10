import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const prisma = new PrismaClient();

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { email, password } = req.body;

  try {
    // Find user by email
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user || !bcrypt.compareSync(password, user.password_hash)) {
      return res.status(401).json({ detail: 'Incorrect email or password' });
    }

    // Create JWT token
    const token = jwt.sign(
      { sub: user.id },
      process.env.SECRET_KEY || 'fallback-secret-key',
      { expiresIn: '30m' }
    );

    res.status(200).json({
      user: {
        id: user.id,
        email: user.email,
        created_at: user.created_at,
        updated_at: user.updated_at
      },
      access_token: token,
      token_type: 'bearer'
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ detail: 'Server error' });
  } finally {
    await prisma.$disconnect();
  }
}