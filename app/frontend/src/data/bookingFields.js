const options = (values) => values.map((value) => ({ value, label: value }))
const number = (name, label, extra = {}) => ({ name, label, type: 'number', min: 0, step: 1, ...extra })
const select = (name, label, values, extra = {}) => ({ name, label, type: 'select', options: options(values), ...extra })
const yesNo = (name, label) => ({ name, label, type: 'select', options: [{ value: 'false', label: 'No' }, { value: 'true', label: 'Yes' }] })

export const sections = [
  { title: 'Booking Details', description: 'The reservation as it stands at booking time.', fields: [
    select('hotel', 'Hotel Type', ['City Hotel', 'Resort Hotel']),
    { name: 'booking_date', label: 'Booking Date', type: 'date' },
    { name: 'arrival_date', label: 'Arrival Date', type: 'date' },
    { name: 'meal', label: 'Meal', type: 'select', options: [
      { value: 'BB', label: 'Bed & breakfast (BB)' }, { value: 'HB', label: 'Half board (HB)' },
      { value: 'FB', label: 'Full board (FB)' }, { value: 'SC', label: 'Self catering (SC)' },
      { value: 'Undefined', label: 'Undefined' },
    ] },
    select('reserved_room_type', 'Reserved Room Type', ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'P'], { hint: 'Use the room category on the reservation.' }),
    select('deposit_type', 'Deposit Type', ['No Deposit', 'Non Refund', 'Refundable']),
  ] },
  { title: 'Stay Details', description: 'Planned nights, daily rate and requested services.', fields: [
    number('stays_in_weekend_nights', 'Weekend Nights'),
    number('stays_in_week_nights', 'Weekday Nights'),
    number('adr', 'Average Daily Rate', { min: undefined, step: 'any', hint: 'Use the recorded daily rate; no currency conversion is applied. Finite negative values are supported.' }),
    number('required_car_parking_spaces', 'Required Car Parking Spaces'),
    number('total_of_special_requests', 'Total Special Requests'),
  ] },
  { title: 'Guest Details', description: 'Guest counts and country of origin.', fields: [
    number('adults', 'Adults'),
    number('children', 'Children', { optional: true, hint: 'Leave blank if unknown.' }),
    number('babies', 'Babies'),
    { name: 'country', label: 'Country', type: 'country', optional: true },
    yesNo('is_repeated_guest', 'Repeated Guest'),
  ] },
  { title: 'Booking Channel', description: 'How this reservation reached the hotel.', fields: [
    { name: 'market_segment', label: 'Market Segment', type: 'select', options: [
      ...options(['Aviation', 'Complementary', 'Corporate', 'Direct', 'Groups']),
      { value: 'Offline TA/TO', label: 'Offline travel agent / tour operator (TA/TO)' },
      { value: 'Online TA', label: 'Online travel agent (TA)' },
      { value: 'Undefined', label: 'Undefined' },
    ] },
    { name: 'distribution_channel', label: 'Distribution Channel', type: 'select', options: [
      ...options(['Corporate', 'Direct']),
      { value: 'GDS', label: 'Global distribution system (GDS)' },
      { value: 'TA/TO', label: 'Travel agent / tour operator (TA/TO)' },
      { value: 'Undefined', label: 'Undefined' },
    ] },
    yesNo('has_agent', 'Booking Through Agent?'),
    yesNo('has_company', 'Booking Through Company?'),
  ] },
  { title: 'Customer History', description: 'Only history known before this reservation.', fields: [
    number('previous_cancellations', 'Previous Cancellations'),
    number('previous_bookings_not_canceled', 'Previous Bookings Not Cancelled'),
    select('customer_type', 'Customer Type', ['Contract', 'Group', 'Transient', 'Transient-Party']),
  ] },
]

export const fields = sections.flatMap((section) => section.fields)
export const fieldLabels = Object.fromEntries(fields.map(({ name, label }) => [name, label]))

function localDate(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

export function initialBooking() {
  const today = new Date()
  const arrival = new Date(today)
  arrival.setDate(arrival.getDate() + 14)
  return {
    hotel: 'City Hotel', booking_date: localDate(today), arrival_date: localDate(arrival),
    meal: 'BB', reserved_room_type: 'A', deposit_type: 'No Deposit',
    stays_in_weekend_nights: '0', stays_in_week_nights: '1', adr: '',
    required_car_parking_spaces: '0', total_of_special_requests: '0',
    adults: '2', children: '0', babies: '0', country: '', is_repeated_guest: 'false',
    market_segment: 'Direct', distribution_channel: 'Direct', has_agent: 'false', has_company: 'false',
    previous_cancellations: '0', previous_bookings_not_canceled: '0', customer_type: 'Transient',
  }
}

export function bookingPayload(values) {
  // Explicit allowlist: send only the 23 request fields, never engineered values.
  return Object.fromEntries(fields.map(({ name, type, optional }) => {
    const value = values[name]
    if (optional && value === '') return [name, null]
    if (type === 'number') return [name, Number(value)]
    if (['is_repeated_guest', 'has_agent', 'has_company'].includes(name)) return [name, value === 'true']
    return [name, value]
  }))
}
