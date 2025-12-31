require('dotenv').config();
require('dotenv').config();
console.log("DEBUG: Your secret is:", process.env.SECRET); // Add this line
const express = require('express');
const { auth, requiresAuth } = require('express-openid-connect');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const axios = require('axios'); // Needed to call the Weather API

const app = express();
app.use(express.urlencoded({ extended: true }));

// 1. Auth0 Configuration
app.use(auth({
    authRequired: false,
    auth0Logout: true,
    issuerBaseURL: process.env.ISSUER_BASE_URL,
    baseURL: process.env.BASE_URL,
    clientID: process.env.CLIENT_ID,
    secret: process.env.SECRET, // <--- This looks for "SECRET" in your .env
    clientSecret: process.env.CLIENT_SECRET, // <--- This looks for "CLIENT_SECRET"
  }));

// 2. HOME PAGE (Public)
app.get('/', (req, res) => {
  res.send(`
    <h1>Global Weather Analytics</h1>
    ${req.oidc.isAuthenticated() ? 
      '<a href="/dashboard">Enter Dashboard</a>' : 
      '<a href="/login">Login to see Weather Data</a>'}
  `);
});

// 3. DASHBOARD (Private - Fetches Weather Data)
app.get('/dashboard', requiresAuth(), async (req, res) => {
  try {
    const city = "London"; // You can change this later to be dynamic
    const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${process.env.WEATHER_API_KEY}&units=metric`;
    const response = await axios.get(weatherUrl);
    const data = response.data;

    res.send(`
      <h1>Dashboard for ${req.oidc.user.name}</h1>
      <p>Current Weather in ${city}: ${data.main.temp}°C, ${data.weather[0].description}</p>
      <hr>
      <form action="/create-checkout-session" method="POST">
        <button type="submit">Upgrade to Pro Analytics</button>
      </form>
    `);
  } catch (error) {
    res.send("Error fetching weather data. Check your API Key in .env");
  }
});

// 4. STRIPE PAYMENTS (The Money Maker)
app.post('/create-checkout-session', requiresAuth(), async (req, res) => {
  const session = await stripe.checkout.sessions.create({
    line_items: [{ price: process.env.STRIPE_PRICE_ID, quantity: 1 }],
    mode: 'subscription',
    success_url: `${process.env.BASE_URL}/dashboard?payment=success`,
    cancel_url: `${process.env.BASE_URL}/dashboard?payment=failed`,
  });
  res.redirect(303, session.url);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server live at http://localhost:${PORT}`));