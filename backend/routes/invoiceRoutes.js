const express = require("express");
const router = express.Router();
const Invoice = require("../models/invoice.js");
const nodemailer = require("nodemailer");
const pdf = require("html-pdf");

function generatePDF(invoice, callback) {
  const html = `
    <h1>Invoice</h1>
    <p>Customer: ${invoice.customerName}</p>
    <p>Total: ₹${invoice.total}</p>
    <p>Payment Method: ${invoice.paymentMethod}</p>
  `;

  pdf.create(html).toBuffer((err, buffer) => {
    if (err) return callback(err);
    callback(null, buffer);
  });
}

router.post("/", async (req, res) => {
  const invoiceData = req.body;
  const invoice = new Invoice(invoiceData);
  await invoice.save();

  generatePDF(invoice, async (err, buffer) => {
    if (err) return res.status(500).json({ error: "PDF generation failed" });

    if (invoice.email) {
      const transporter = nodemailer.createTransport({
        service: "gmail",
        auth: {
          user: process.env.EMAIL_USER,
          pass: process.env.EMAIL_PASS,
        },
      });

      const mailOptions = {
        from: process.env.EMAIL_USER,
        to: invoice.email,
        subject: "Your e-Invoice",
        text: `Hello ${invoice.customerName}, your invoice total is ₹${invoice.total}`,
        attachments: [{ filename: "invoice.pdf", content: buffer }],
      };

      transporter.sendMail(mailOptions, (error, info) => {
        if (error) console.error(error);
        else console.log("Email sent: " + info.response);
      });
    }

    res.status(201).json({ message: "Invoice saved and email sent" });
  });
});

router.get("/", async (req, res) => {
  const invoices = await Invoice.find().sort({ createdAt: -1 });
  res.json(invoices);
});

module.exports = router;
