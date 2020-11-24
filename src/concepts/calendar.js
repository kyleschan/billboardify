import moment from "moment";

const DATE_STRING_END = 10;
const WEDNESDAY_ISO_INT = 3;
const SATURDAY_ISO_INT = 6;

export const addDays = (date, days) => {
  var newDate = new Date(date);
  newDate.setDate(newDate.getDate() + days);
  return newDate;
}

export const adjustDate = date => {
  var newDate = addDays(date, WEDNESDAY_ISO_INT - date.getDay());
  const today = new Date(moment().toDate());
  return newDate <= today ? newDate : addDays(newDate, -7);
}

export const toSaturday = dateStr => {
  const oldDate = new Date(dateStr);
  return dateString(addDays(oldDate, SATURDAY_ISO_INT - oldDate.getDay()));
}

export const dateString = date => moment(date).format().substring(0, DATE_STRING_END);