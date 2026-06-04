import "./globals.css";

// Removida a importação do Header daqui

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-br">
      <body className="antialiased">
        {/* Removido o <Header /> daqui para não duplicar na Home e sumir do Chat */}
        {children}
      </body>
    </html>
  );
}