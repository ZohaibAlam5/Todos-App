import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const prisma = new PrismaClient();

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { email, code, new_password } = req.body;

  try {
    // Validate the reset code
    const resetToken = await prisma.passwordResetToken.findFirst({
      where: {
        email,
        token: code,
        used: false,
        expiresAt: {
          gte: new Date() // Check that it hasn't expired
        }
      }
    });

    if (!resetToken) {
      return res.status(400).json({ detail: 'Invalid or expired reset code' });
    }

    // Validate the new password
    if (!validatePassword(new_password)) {
      return res.status(400).json({ detail: 'Password does not meet requirements' });
    }

    // Hash the new password
    const hashedPassword = await bcrypt.hash(new_password, 10);

    // Update the user's password
    await prisma.user.update({
      where: { email },
      data: { password_hash: hashedPassword }
    });

    // Mark the reset token as used
    await prisma.passwordResetToken.update({
      where: { id: resetToken.id },
      data: { used: true }
    });

    res.status(200).json({ message: 'Password reset successfully' });
  } catch (error) {
    console.error('Reset password error:', error);
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