import React, { useState } from "react";

import { CheckboxInput } from "../../forms/inputs";


const checkBoxFields = (fields) => Object.entries(fields).map(([name, value]) => typeof value === 'string'
            ? <CheckboxInput key={name} name={name} id={name}/>
            : <div key={name}><h3>{name}</h3><div style={{marginLeft: '20px'}}>{checkBoxFields(value)}</div></div>);


const PermissionForm = (props) => {
    const {objectFields, dataFields} = props;

    return (
        <fieldset className="module aligned">
            <h2>Fields allowed to display</h2>

            { checkBoxFields(objectFields) }

        </fieldset>
    );
};


export { PermissionForm };
