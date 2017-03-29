# In this quiz, there's a table describing bugs in various files of code.
# Here's what the table looks like:
#
# create table programs (
#    name text,
#    filename text
# );
# create table bugs (
#    filename text,
#    description text,
#    id serial primary key
# );
#
# The query below is intended to count the number of bugs in each program. But
# it doesn't return a row for any program that has zero bugs.  Try running it as
# it is; then change it so that it includes rows for the programs with no bugs.

QUERY = '''
select programs.name, count(bugs.id) as num
  from programs left join bugs
    on programs.filename = bugs.filename
 group by programs.name
 order by num;
'''
