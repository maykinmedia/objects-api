import React, { useState } from "react";


const CheckboxInput = ({name, id, checked, label, onChange}) => {
    return (
        <div className="checkbox-row">
            <input
                type="checkbox"
                id={id}
                name={name}
                checked={checked}
                onChange={(event) => {
                    if (onChange) {
                        onChange(event);
                    }
                }}
            />
            <label className="vCheckboxLabel" htmlFor={id}>{ label }</label>
        </div>
    );
};


const TextInput = (props) => {
    const { id, name, initial, label } = props;
    const [value, setValue] = useState(initial || "");

    return (
         <div>
             <label htmlFor={id}>{label}</label>
            <input
                type="text"
                id={id}
                name={name}
                onChange={ (event) => {
                    setValue(event.text);
                }}
                defaultValue={value}
            />
         </div>
    );
};


const SelectInput = (props) => {
    const { choices, name, id, label, onChange, initialValue } = props;

    const [currentValue, setCurrentValue] = useState(initialValue || "");

    const options = choices.map( ([value, label], index) =>
        <option key={index} value={value}>{label}</option>
    );

    return (
        <div>
            <label className="required" htmlFor={id}>{label}</label>
            <select
                name={name}
                required={true}
                id={id}
                value={currentValue}
                onChange={ (event, value) => {
                    setCurrentValue(value);
                    if (onChange) {
                        onChange(value);
                    }
                }}
            >
                {options}
            </select>
        </div>
    )
}

export { CheckboxInput, TextInput, SelectInput };
