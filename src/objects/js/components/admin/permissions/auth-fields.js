import React from "react";

import {CheckboxInput} from "../../forms/inputs";


const add = (value, arr, setState) => {
    if (arr.includes(value)) {
        return;
    }
    const newArr = [...arr];
    newArr.push(value);

    setState(newArr);
};

const remove = (value, arr, setState) => {
    if (!arr.includes(value)) {
        return;
    }
    const newArr = arr.filter(x => x !== value);
    setState(newArr);
};


const authFields = (object_fields, dataFields, fields, setFields) => {
    if (!object_fields) return;

    return Object.entries(object_fields).map(([name, field_id]) => {
        if (field_id === 'record__data') {
           return <div key={name}>
                <h3>{name}</h3>
                <div className="permission-fields__nested">
                    {authFields(dataFields, dataFields, fields, setFields)}
                </div>
            </div>;

        } else if (typeof field_id === 'string') {
           return <CheckboxInput
                key={field_id}
                name={name}
                id={field_id}
                label={name}
                value={fields.includes(field_id)}
                onChange={(value) => {
                    if (value) {
                        add(field_id, fields, setFields);
                    } else {
                        remove(field_id, fields, setFields);
                    }
                }}
            />;
        } else {
            return <div key={name}>
                <h3>{name}</h3>
                <div className="permission-fields__nested">
                    { authFields(field_id, dataFields, fields, setFields) }
                </div>
            </div>;
        }
    });
};


export { authFields };
