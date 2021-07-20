import React, { useState } from "react";


const CheckboxInput = ({name, id, value, label, onChange}) => {
    return (
        <div className="checkbox-row">
            <input
                type="checkbox"
                id={id}
                name={name}
                checked={value}
                onChange={(event ) => {
                    if (onChange) {
                        onChange(event.target.checked);
                    }
                }}
            />
            {label ? <label className="vCheckboxLabel" htmlFor={id}>{ label }</label> : null}
        </div>
    );
};


const TextInput = (props) => {
    const { id, name, value, label, onChange, hidden } = props;

    return (
         <div>
             {label ? <label htmlFor={id}>{label}</label> : null}
            <input
                type="text"
                id={id}
                name={name}
                hidden={hidden}
                onChange={ (event) => {
                    if (onChange) {
                        onChange(event.target.value);
                    }
                }}
                value={value}
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
                        onChange(event.target.value);
                    }
                }}
            >
                {options}
            </select>
        </div>
    )
}

export { CheckboxInput, TextInput, SelectInput };
