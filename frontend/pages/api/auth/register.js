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
    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      return res.status(400).json({ detail: 'Email already registered' });
    }

    // Validate password
    if (!validatePassword(password)) {
      return res.status(400).json({ detail: 'Password does not meet requirements' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        password_hash: hashedPassword
      }
    });

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
    console.error('Registration error:', error);
    res.status(500).json({ detail: 'Server error' });
  } finally {
    await prisma.$disconnect();
  }
}

function validatePassword(password) {
  if (password.length < 8) return false;
  if (!/[A-Z]/.test(password)) return false;
  if (!/[a-z]/.test(password)) return false;
  if (!/\d/.test(password)) return false;
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return false;
  return true;
}