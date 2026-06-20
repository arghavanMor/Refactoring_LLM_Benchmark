assert(this.discountRate >= 0);
if (this.discountRate)
  base = base - (this.discountRate * base);