const mongoose = require("mongoose");

const invoiceSchema = new mongoose.Schema({
  customerName: String,
  email: String,
  phone: String,
  total: Number,
  paymentMethod: String,
  createdAt: { type: Date, default: Date.now },
});

module.exports = mongoose.model("Invoice", invoiceSchema);
