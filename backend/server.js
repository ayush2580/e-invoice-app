const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const connectDB = require("./db");
const invoiceRoutes = require("./routes/invoiceRoutes");
const app = express();
const PORT = 5000;

require("dotenv").config();

connectDB();

app.use(cors());
app.use(bodyParser.json());
app.use("/api/invoices", invoiceRoutes);

app.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));