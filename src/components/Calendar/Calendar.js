import React, {useState} from 'react';
import moment from "moment";
import DatePicker from "react-datepicker";
import CalendarInput from './CalendarInput';
import "react-datepicker/dist/react-datepicker.css";

const BEG_DATE = '1980-01-02';

// CSS Modules, react-datepicker-cssmodules.css
// import 'react-datepicker/dist/react-datepicker-cssmodules.css';


export const Calendar = ({onSelection}) => {
  const [currentDate, setCurrentDate] = useState(new Date(moment().toDate()));
  return (
    <DatePicker
    selected={currentDate}
    onChange={date => onSelection(date, setCurrentDate)}
    minDate={new Date(BEG_DATE)}
    maxDate={new Date()}
    customInput={<CalendarInput />}
    showMonthDropdown
    showYearDropdown
    dropdownMode="select"/>
  );
};