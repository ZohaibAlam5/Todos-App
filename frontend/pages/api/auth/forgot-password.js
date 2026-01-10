import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const prisma = new PrismaClient();

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { email } = req.body;

  try {
    // Find the user (don't reveal if email exists for security)
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (user) {
      // Generate a secure reset code (6 digits)
      const resetCode = Math.floor(100000 + Math.random() * 900000).toString();

      // Store the reset code and expiry time (15 minutes from now)
      const expiryTime = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

      // Remove any existing reset tokens for this email
      await prisma.passwordResetToken.deleteMany({
        where: { email }
      });

      // Create a new reset token
      await prisma.passwordResetToken.create({
        data: {
          email,
          token: resetCode,
          expiresAt: expiryTime,
          used: false
        }
      });

      // In a real application, you would send an email with the reset code
      // For now, we'll just log it (in production, use an email service like SendGrid, Nodemailer, etc.)
      console.log(`Password reset code for ${email}: ${resetCode}`);

      // Simulate email sending delay
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Always return success to prevent email enumeration
    res.status(200).json({ message: 'Password reset code sent successfully' });
  } catch (error) {
    console.error('Forgot password error:', error);
    res.status(500).json({ detail: 'Server error' });
  } finally {
    await prisma.$disconnect();
  }
}