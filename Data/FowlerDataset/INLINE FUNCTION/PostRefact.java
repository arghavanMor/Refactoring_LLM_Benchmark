function getRating(driver) {
  return (driver.numberOfLateDeliveries > 5) ? 2 : 1;
}