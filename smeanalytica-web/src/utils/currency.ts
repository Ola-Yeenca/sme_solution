interface CurrencyInfo {
  symbol: string;
  code: string;
  position: 'before' | 'after';
}

const CURRENCY_MAP: { [key: string]: CurrencyInfo } = {
  'US': { symbol: '$', code: 'USD', position: 'before' },
  'GB': { symbol: '£', code: 'GBP', position: 'before' },
  'ES': { symbol: '€', code: 'EUR', position: 'after' },
  'FR': { symbol: '€', code: 'EUR', position: 'after' },
  'DE': { symbol: '€', code: 'EUR', position: 'after' },
  'IT': { symbol: '€', code: 'EUR', position: 'after' },
  'JP': { symbol: '¥', code: 'JPY', position: 'before' },
  'CN': { symbol: '¥', code: 'CNY', position: 'before' },
  'IN': { symbol: '₹', code: 'INR', position: 'before' },
  'BR': { symbol: 'R$', code: 'BRL', position: 'before' },
};

export function getCurrencyInfoFromLocation(location: string): CurrencyInfo {
  // Default to EUR for European locations
  let defaultCurrency: CurrencyInfo = { symbol: '€', code: 'EUR', position: 'after' };
  
  if (!location) return defaultCurrency;
  
  // Extract country code from location (e.g., "Valencia, Spain" -> "ES")
  const countryMap: { [key: string]: string } = {
    'spain': 'ES',
    'united states': 'US',
    'usa': 'US',
    'united kingdom': 'GB',
    'uk': 'GB',
    'france': 'FR',
    'germany': 'DE',
    'italy': 'IT',
    'japan': 'JP',
    'china': 'CN',
    'india': 'IN',
    'brazil': 'BR',
  };
  
  const locationLower = location.toLowerCase();
  let countryCode = '';
  
  // Try to find country code from the location string
  for (const [country, code] of Object.entries(countryMap)) {
    if (locationLower.includes(country)) {
      countryCode = code;
      break;
    }
  }
  
  return CURRENCY_MAP[countryCode] || defaultCurrency;
}

export function formatPrice(amount: number, location: string): string {
  const currencyInfo = getCurrencyInfoFromLocation(location);
  const formattedAmount = amount.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  return currencyInfo.position === 'before'
    ? `${currencyInfo.symbol}${formattedAmount}`
    : `${formattedAmount}${currencyInfo.symbol}`;
}
