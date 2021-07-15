import React from "react";


const CheckboxInput = ({name, id, checked, onChange}) => {
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
            <label className="vCheckboxLabel" htmlFor={id}>{ name }</label>
        </div>
    );
};


export { CheckboxInput };
