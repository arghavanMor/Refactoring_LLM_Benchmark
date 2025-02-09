function totalOutstanding() {
  return customer.invoices.reduce((total, each) => each.amount + total, 0);  
}
function sendBill() {
  emailGateway.send(formatBill(customer));
}