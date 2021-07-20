import React, { useState } from "react";

import { CheckboxInput, TextInput, SelectInput } from "../../forms/inputs";


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


const checkBoxFields = (object_fields, fields, setFields) => {
    return Object.entries(object_fields).map(([name, field_id]) =>
        typeof field_id === 'string'
            ? <CheckboxInput
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
            />
            : <div key={name}>
                <h3>{name}</h3>
                <div style={{marginLeft: '20px'}}>
                    {checkBoxFields(field_id, fields, setFields)}
                </div>
            </div>
    );
};


const PermissionForm = (props) => {
    const {objectFields, dataFieldChoices, tokenChoices, objecttypeChoices, modeChoices, initialData} = props;

    const [useFields, setUseFields] = useState(initialData["use_fields"]);
    const [fields, setFields] = useState(initialData["fields"].split(","));
    // const [dataFields, setDataFields] = useState()

    return (
         <>
         <fieldset className="module aligned">
            <div className="form-row">
                <SelectInput
                    name="token_auth"
                    id="id_token_auth"
                    label="Token auth:"
                    choices={tokenChoices}
                    initialValue={initialData["token_auth"]}
                />
            </div>

            <div className="form-row">
                <SelectInput
                    name="object_type"
                    id="id_object_type"
                    label="Object type:"
                    choices={objecttypeChoices}
                    initialValue={initialData["object_type"]}
                />
            </div>

            <div className="form-row">
                <SelectInput
                    name="mode"
                    id="id_mode"
                    label="Mode:"
                    choices={modeChoices}
                    initialValue={initialData["mode"]}
                />

            </div>

            <div className="form-row">
                <CheckboxInput
                    name="use_fields"
                    id="id_use_fields"
                    label="Use fields"
                    value={useFields}
                    onChange={(value) => {setUseFields(value)}}
                />
            </div>

            <div className="form-row">
                <TextInput
                    name="fields"
                    id="id_fields"
                    label="Fields:"
                    value={useFields ? fields : ""}/>
            </div>

        </fieldset>

        { useFields ?

            <fieldset className="module aligned">
                <h2>Fields allowed to display</h2>
                { checkBoxFields(objectFields, fields, setFields) }
            </fieldset>

            : null
        }
        </>
    );
};


export { PermissionForm };
