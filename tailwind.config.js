/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", // Escanea todos los archivos HTML en la carpeta 'templates'
    "./static/**/*.js" // Si tienes JS con clases de Tailwind
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}