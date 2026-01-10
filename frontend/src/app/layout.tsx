import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/components/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TaskFlow - A Todo App",
  description: "Futuristic Task Management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const storageKey = 'theme'; // Must match the key in your ThemeContext
                  const className = 'dark';
                  
                  const localTheme = localStorage.getItem(storageKey);
                  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
                  
                  // Check if user has manually set a theme, or default to system
                  if (localTheme === 'dark' || (!localTheme && systemTheme)) {
                    document.documentElement.classList.add(className);
                  } else {
                    document.documentElement.classList.remove(className);
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>

      <body className={`${inter.className} bg-gray-50 dark:bg-gray-950 transition-colors duration-500`}>
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}