import type { Metadata } from "next";
import { Toaster } from "sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "NCIA | National Cyber Crime Reporting System",
  description: "Official portal for reporting cyber crimes in Pakistan under PECA 2016.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
        <main className="flex-1 flex flex-col">
          {children}
        </main>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
