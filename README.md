# Tools For Use With ESGF

The Earth System Grid Federation is a large database management system for climate science data. These tools are useful for data integrity checking and other tasks in regard to this project.

# The CMIP6 Inconsistency Checker (CIC)

The program cic.py systematically queries ESGF CMIP6 data looking for incorrectly stored data records. There are several errors it looks for:
 - duplicate records
 - inconsistent numbers of files across records in the same instance_id group
 - replicas with no original record
 - replicas with multiple original records (see also duplicates)
 - records which have an activity_id which is not in the CMOR tables
 - records which have an activity_id which does not agree with the experiment_id according to the CMOR tables
 - records which have the original record flagged not latest when the replicas are, meaning they need to be flagged not latest
 - records which have the original record retracted and the replicas are not, as well as vice versa

These errors are used to sort output into a json dictionary which is saved as ``inconsistencies.json`` in addition to separate smaller documents which save the output organized by data node and corresponding error (also in json format). An email summary is also sent to a predetermined list of international collaborators on the ESGF project as well as two of the LLNL ESGF team members. This can be changed towards the end of the program.

# Data Node Certificate Expiration Notification Program

The program dn_status.py queries for the ssl certification expiration on each of the ESGF data nodes. It generates an email summary of when each one expires. The final version will send notifications to the proper emails when their data node ssl certificate is close to expiring.
