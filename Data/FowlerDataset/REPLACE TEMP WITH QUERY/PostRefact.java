get basePrice() {this._quantity * this._itemPrice;}

// ...

if (this.basePrice > 1000)
  return this.basePrice * 0.95;
else
  return this.basePrice * 0.98;