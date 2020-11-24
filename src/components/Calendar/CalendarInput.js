
import React from 'react';


export default ({ value, onClick }) => (
    <button className="btn-dark" onClick={onClick}>
      {value}
    </button>
  );