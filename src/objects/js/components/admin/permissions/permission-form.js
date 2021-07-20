import React, { useState } from "react";

import { CheckboxInput, TextInput, SelectInput } from "../../forms/inputs";


const checkBoxFields = (fields) => Object.entries(fields).map(([name, value]) => typeof value === 'string'
            ? <CheckboxInput key={value} name={name} id={value} label={name}/>
            : <div key={name}><h3>{name}</h3><div style={{marginLeft: '20px'}}>{checkBoxFields(value)}</div></div>);


const PermissionForm = (props) => {
    const {objectFields, dataFields, tokenChoices, objecttypeChoices, modeChoices} = props;

    return (
         <>
         <fieldset className="module aligned">
            <div className="form-row">
                <SelectInput name="token_auth" id="id_token_auth" label="Token auth:" choices={tokenChoices}/>
            </div>

            <div className="form-row">
                <SelectInput name="object_type" id="id_object_type" label="Object type:" choices={objecttypeChoices}/>
            </div>

            <div className="form-row">
                <SelectInput name="mode" id="id_mode" label="Mode:" choices={modeChoices}/>

            </div>

            <div className="form-row">
                <CheckboxInput name="Use fields" id="id_use_fields" label="Use fields"/>
            </div>

            <div className="form-row">
                <TextInput name="fields" id="id_fields" label="Fields:"/>
            </div>

        </fieldset>
        <fieldset className="module aligned">
            <h2>Fields allowed to display</h2>

            { checkBoxFields(objectFields) }

        </fieldset>
        </>
    );
};


export { PermissionForm };
