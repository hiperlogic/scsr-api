"""
    The Models Package contains the Database Model (DB) and the Application Object (AO) model.
        - The Application Object model must contain all the fields of the DB model and vice versa.
        - The DB Model must provide the data to save to the Database and to update referenced models.
        - The AO Model must deal only with its own representation.
            The last 2 rules may be noticeable in the usergamesgenre db object. The AO only deals with the object, whence the DB
            invokes the methods to update game accounting data.
        - The DB Model must provide methods to return an AO object
        - The DB Model must provide methods to receive data from an AO object and construct the referenced DB object.
"""
