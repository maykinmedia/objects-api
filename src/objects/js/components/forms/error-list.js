// SPDX-License-Identifier: EUPL-1.2
// Copyright (C) 2020 Dimpact
import React from 'react';


const ErrorList = (props) => {
    const { errors } = props;
    if (!errors.length) return null;

    return (
        <ul className="errorlist">
            { errors.map( (err, index) => <li key={index}>{ err.msg }</li> ) }
        </ul>
    );
};


export { ErrorList };
