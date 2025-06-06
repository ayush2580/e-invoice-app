
import { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [invoice, setInvoice] = useState({
    customerName: "",
    email: "",
    phone: "",
    total: "",
    paymentMethod: "CASH",
  });
  const [invoices, setInvoices] = useState([]);

  const handleChange = (e) => {
    setInvoice({ ...invoice, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:5000/api/invoices", invoice);
      alert(res.data.message);
      fetchInvoices();
    } catch (err) {
      alert("Failed to send invoice");
    }
  };

  const fetchInvoices = async () => {
    const res = await axios.get("http://localhost:5000/api/invoices");
    setInvoices(res.data);
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-xl font-bold mb-4">E-Invoice Generator</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input name="customerName" onChange={handleChange} placeholder="Customer Name" className="w-full p-2 border" />
        <input name="email" onChange={handleChange} placeholder="Email" className="w-full p-2 border" />
        <input name="phone" onChange={handleChange} placeholder="Phone (for SMS/WhatsApp)" className="w-full p-2 border" />
        <input name="total" onChange={handleChange} placeholder="Invoice Total" className="w-full p-2 border" />
        <select name="paymentMethod" onChange={handleChange} className="w-full p-2 border">
          <option value="CASH">Cash</option>
          <option value="UPI">UPI</option>
        </select>
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">Send Invoice</button>
      </form>

      <div className="mt-6">
        <h2 className="text-lg font-bold">Saved Invoices</h2>
        <ul className="mt-2 space-y-2">
          {invoices.map((inv) => (
            <li key={inv._id} className="p-2 border rounded">
              <p><strong>{inv.customerName}</strong> - ₹{inv.total}</p>
              <p>{inv.paymentMethod} | {new Date(inv.createdAt).toLocaleString()}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
