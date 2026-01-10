'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/components/AuthContext';
import { authService } from '@/services/auth'; // Import service directly for reset calls
import { Mail, Lock, LogIn, UserPlus, ArrowRight, Loader2, KeyRound, ChevronLeft } from 'lucide-react';

interface AuthFormProps {
  mode: 'login' | 'register';
}

const AuthForm: React.FC<AuthFormProps> = ({ mode: initialMode }) => {
  // --- STATES ---
  // We use a local view state to switch between Login, Register, and Forgot without changing URL
  const [view, setView] = useState<'login' | 'register' | 'forgot'>(initialMode);
  const [forgotStep, setForgotStep] = useState<'email' | 'reset'>('email');
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [resetCode, setResetCode] = useState(''); // New State for Code
  
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState(''); // To show "Code sent!"
  const [loading, setLoading] = useState(false);
  
  const router = useRouter();
  const { login, register } = useAuth();

  // Helper to check current view
  const isLogin = view === 'login';
  const isRegister = view === 'register';
  const isForgot = view === 'forgot';

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return false;
    }
    return true;
  };

  const validatePassword = (password: string): boolean => {
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    return true;
  };

  // --- HANDLER: FORGOT PASSWORD FLOW ---
  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setLoading(true);

    try {
      if (forgotStep === 'email') {
        // STEP 1: Request Code
        if (!validateEmail(email)) { setLoading(false); return; }
        
        await authService.requestPasswordReset(email);
        setSuccessMessage(`if your email is correct and registered, you will receive a reset code at ${email}`);
        setForgotStep('reset'); // Move to next step
      } else {
        // STEP 2: Verify & Reset
        if (!resetCode.trim()) { setError("Please enter the code"); setLoading(false); return; }
        if (!validatePassword(password)) { setLoading(false); return; }
        if (password !== confirmPassword) { setError("Passwords do not match"); setLoading(false); return; }

        await authService.resetPassword(email, resetCode, password);
        setSuccessMessage("Password reset successfully! Please login.");
        setTimeout(() => {
           setView('login'); // Redirect to login view
           setPassword('');
           setResetCode('');
        }, 2000);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  // --- HANDLER: LOGIN / REGISTER FLOW ---
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!validateEmail(email)) { setLoading(false); return; }

      if (isLogin) {
        await login(email, password);
        router.push('/dashboard');
      } else {
        if (password !== confirmPassword) {
          setError('Passwords do not match'); setLoading(false); return;
        }
        if (!validatePassword(password)) { setLoading(false); return; }
        await register(email, password);
        router.push('/dashboard');
      }
    } catch (err) {
      console.error("Caught error:", err);
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(typeof message === 'object' ? JSON.stringify(message) : message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-100 dark:bg-[#0a0e17] p-4 sm:p-6 md:p-12 lg:p-6 relative overflow-hidden transition-colors duration-500">
      
      {/* Background Ambience */}
      <div className="absolute top-[-20%] right-[-10%] w-150 h-150 bg-indigo-500/30 dark:bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-20%] left-[-10%] w-150 h-150 bg-purple-500/30 dark:bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Main Card Container */}
      <div className="w-full max-w-5xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-[30px] overflow-hidden shadow-2xl border border-white/50 dark:border-white/10 flex flex-col lg:flex-row min-h-150 relative z-10 transition-colors duration-500">
        
        {/* LEFT SIDE: Branding */}
        <div className="flex w-full lg:w-1/2 relative bg-gray-50/50 dark:bg-gray-900 flex-col items-center justify-center p-8 md:p-16 lg:p-12 overflow-hidden border-b lg:border-b-0 lg:border-r border-gray-200 dark:border-white/5 transition-colors duration-500">
           {/* Glow behind logo */}
           <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full blur-[80px] 
             ${isLogin ? 'bg-indigo-500/40 dark:bg-indigo-500/20' : 'bg-purple-500/40 dark:bg-purple-500/20'}`} 
           />
           
           <div className="relative z-10 flex flex-col items-center text-center space-y-6 md:space-y-8 lg:space-y-6">
              <div className={`w-20 h-20 md:w-32 md:h-32 lg:w-24 lg:h-24 rounded-3xl flex items-center justify-center shadow-lg transition-all duration-500 bg-linear-to-br from-indigo-500 to-purple-600 shadow-indigo-500/30`}>
                {isForgot ? (
                   <KeyRound className="w-8 h-8 md:w-14 md:h-14 lg:w-10 lg:h-10 text-white stroke-[2.5]" />
                ) : isLogin ? (
                  <LogIn className="w-8 h-8 md:w-14 md:h-14 lg:w-10 lg:h-10 text-white stroke-[2.5] ml-1" />
                ) : (
                  <UserPlus className="w-8 h-8 md:w-14 md:h-14 lg:w-10 lg:h-10 text-white stroke-[2.5]" />
                )}
              </div>
              
              <div className="space-y-2 md:space-y-3">
                <h1 className="text-3xl md:text-5xl lg:text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight transition-colors duration-300">
                  {isForgot ? <>Reset <br /> Password</> : isLogin ? <>Welcome <br /> Back</> : <>Join <br /> TaskFlow</>}
                </h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm md:text-lg lg:text-sm font-medium transition-colors duration-300 max-w-xs mx-auto">
                  {isForgot ? 'Securely recover your account access.' : isLogin ? 'Your personal futuristic workspace.' : 'Start your journey with us today.'}
                </p>
              </div>
           </div>
        </div>

        {/* RIGHT SIDE: Form */}
        <div className="w-full lg:w-1/2 relative flex items-center justify-center p-8 md:p-16 lg:p-12 bg-white/50 dark:bg-gray-900/50 transition-colors duration-500">
          <div className="w-full max-w-sm md:max-w-md lg:max-w-sm space-y-8 relative z-10">
            
            {/* Header */}
            <div className="text-center space-y-2">
              <h2 className="text-3xl md:text-4xl lg:text-3xl font-bold bg-clip-text text-transparent bg-linear-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
                {isForgot ? (forgotStep === 'email' ? 'Forgot Password?' : 'Reset Password') : (isLogin ? 'Sign In' : 'Create Account')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 text-sm md:text-base lg:text-sm">
                {isForgot 
                  ? (forgotStep === 'email' ? 'Enter your email to receive a reset code.' : 'Enter the code sent to your email.') 
                  : (isLogin ? 'Enter your credentials to access the system.' : 'Fill in your details to register.')}
              </p>
            </div>

            <form onSubmit={isForgot ? handleForgotSubmit : handleAuthSubmit} className="space-y-5 md:space-y-6">
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 px-4 py-2 rounded-xl text-sm text-center animate-in fade-in slide-in-from-top-2">
                  {error}
                </div>
              )}
              {successMessage && (
                <div className="bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400 px-4 py-2 rounded-xl text-sm text-center animate-in fade-in slide-in-from-top-2">
                  {successMessage}
                </div>
              )}

              <div className="space-y-4 md:space-y-5">
                
                {/* --- INPUTS FOR FORGOT PASSWORD MODE --- */}
                {isForgot ? (
                  <>
                    {/* Step 1: Email (Always shown or read-only in step 2) */}
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                      </div>
                      <input
                        type="email"
                        required
                        disabled={forgotStep === 'reset'} // Lock email in step 2
                        className={`block w-full pl-11 pr-4 py-3.5 bg-gray-50 dark:bg-gray-800/50 border rounded-2xl focus:outline-none focus:ring-2 transition-all 
                          ${forgotStep === 'reset' ? 'border-gray-200 dark:border-gray-700 opacity-60 cursor-not-allowed text-gray-500' : 'border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-200 focus:ring-indigo-500/50 focus:border-indigo-500'}`}
                        placeholder="Email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </div>

                    {/* Step 2: Code & New Password */}
                    {forgotStep === 'reset' && (
                      <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
                        <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <KeyRound className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                          </div>
                          <input
                            type="text"
                            required
                            className="block w-full pl-11 pr-4 py-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                            placeholder="Enter 6-digit Code"
                            value={resetCode}
                            onChange={(e) => setResetCode(e.target.value)}
                          />
                        </div>
                        <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <Lock className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                          </div>
                          <input
                            type="password"
                            required
                            className="block w-full pl-11 pr-4 py-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                            placeholder="New Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                          />
                        </div>
                        <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <Lock className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                          </div>
                          <input
                            type="password"
                            required
                            className="block w-full pl-11 pr-4 py-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                            placeholder="Confirm New Password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                          />
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  // --- INPUTS FOR LOGIN/REGISTER MODE ---
                  <>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 md:h-6 md:w-6 lg:h-5 lg:w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-indigo-600 dark:group-focus-within:text-indigo-400 transition-colors" />
                      </div>
                      <input
                        id="email"
                        type="email"
                        required
                        className="block w-full pl-11 md:pl-12 pr-4 py-3.5 md:py-4 lg:py-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all sm:text-sm md:text-base lg:text-sm"
                        placeholder="Email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </div>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 md:h-6 md:w-6 lg:h-5 lg:w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-indigo-600 dark:group-focus-within:text-indigo-400 transition-colors" />
                      </div>
                      <input
                        id="password"
                        type="password"
                        required
                        className="block w-full pl-11 md:pl-12 pr-4 py-3.5 md:py-4 lg:py-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all sm:text-sm md:text-base lg:text-sm"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                    </div>
                    {!isLogin && (
                      <div className="relative group">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <Lock className="h-5 w-5 md:h-6 md:w-6 lg:h-5 lg:w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-indigo-600 dark:group-focus-within:text-indigo-400 transition-colors" />
                        </div>
                        <input
                          id="confirm-password"
                          type="password"
                          required
                          className="block w-full pl-11 md:pl-12 pr-4 py-3.5 md:py-4 lg:py-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all sm:text-sm md:text-base lg:text-sm"
                          placeholder="Confirm Password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Forgot Password Link (Only in Login Mode) */}
              {isLogin && !isForgot && (
                <div className="flex justify-end">
                  <button 
                    type="button"
                    onClick={() => { setView('forgot'); setForgotStep('email'); setError(''); }}
                    className="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors"
                  >
                    Forgot Password?
                  </button>
                </div>
              )}

              {/* Action Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center items-center py-3.5 md:py-4 lg:py-3.5 px-4 text-white text-sm md:text-lg lg:text-sm font-bold rounded-full transition-all transform hover:scale-[1.01] disabled:opacity-70 disabled:cursor-not-allowed mt-6 bg-linear-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/30"
              >
                {loading ? (
                  <Loader2 className="animate-spin h-5 w-5" />
                ) : (
                  <span className="flex items-center gap-2">
                    {isForgot 
                      ? (forgotStep === 'email' ? 'Send Reset Code' : 'Reset Password') 
                      : (isLogin ? 'Sign In' : 'Create Account')
                    }
                    <ArrowRight className="h-4 w-4 md:h-5 md:w-5 lg:h-4 lg:w-4" />
                  </span>
                )}
              </button>
            </form>

            {/* Bottom Links */}
            <div className="text-center mt-6">
              {isForgot ? (
                <button
                  type="button"
                  onClick={() => { setView('login'); setError(''); setSuccessMessage(''); }}
                  className="flex items-center justify-center gap-2 mx-auto text-sm text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" /> Back to Login
                </button>
              ) : (
                <p className="text-sm md:text-base lg:text-sm text-gray-500 dark:text-gray-400">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    type="button"
                    onClick={() => { setView(isLogin ? 'register' : 'login'); setError(''); }}
                    className="font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors ml-1"
                  >
                    {isLogin ? 'Register now' : 'Log in'}
                  </button>
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthForm;