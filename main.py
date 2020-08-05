import sympy as sp

def interval(generators, lattice_pos):
    """Find reduced intervals of lattice positions.

        Given generators and lattice positions returns the reduced intervals of the positions.

        Parameters
        ----------
        generators : Matrix
            Column vector with the non-reduced generator intervals of the lattice.
        lattice_pos : Matrix
            Matrix with lattice positions of the intervals on the rows.

        Returns
        -------
        Matrix
            Column vector with the same number of elements as rows in lattice_pos where each element
            is the reduced fraction corresponding to the matrix positions in the rows of lattice_pos.

        Examples
        --------
        >>> generators = sp.Matrix([[5],[3]])
        >>> comma_positions = sp.Matrix([[-1,4],[-3,0]])
        >>> print(interval(generators, comma_positions))
        Matrix([[81/80], [128/125]])
        """
    if isinstance(lattice_pos, sp.Matrix):
        output = sp.ones(lattice_pos.shape[0], 1)

        for i in range(lattice_pos.rows):
            row = lattice_pos.row(i)
            #print(row)
            #print(generators)
            for j in range(len(row)):
                output[i] *= generators[j] ** row[j]
                while output[i] < 1 or output[i] > 2:
                    if output[i] < 1:
                        output[i] *= 2
                    else:
                        output[i] /= 2
    elif isinstance(lattice_pos, sp.Point2D):
        output = sp.ones(1, 1)
        output *= generators[0] ** lattice_pos.x
        output *= generators[1] ** lattice_pos.y
        while output[0] < 1 or output[0] > 2:
            if output[0] < 1:
                output *= 2
            else:
                output /= 2


    return output

def is_in_block(test, comma_positions, include_commas):
    dim = len(comma_positions.row(0))

    if len(comma_positions) != dim ** 2:
        raise ValueError('The number of commas should be the same as the dimensionality of the lattice.')

    block = sp.Polygon(sp.Point([0,0]),
                       sp.Point(comma_positions.row(0)),
                       sp.Point(comma_positions.row(0) + comma_positions.row(1)),
                       sp.Point(sp.Point(comma_positions.row(1))))

    if test in block.vertices and test != sp.Point2D(0,0):
        return include_commas  # Does not include commas in output

    for side in block.sides:
        if side.contains(test):
            return True

    return block.encloses_point(test)

    # block_area = block.area
    # checksum = 0
    # for side in block.sides:
    #     triangle = sp.Polygon(side.points[0], side.points[1], sp.Point(test))
    #     if not isinstance(triangle, sp.Segment2D):
    #         checksum += abs(triangle.area)
    # return checksum == block_area

def scl_output(filename, commas, interval_list):
    file = open(filename+'.scl','w')
    file.write('! Created by Fredrik Hallhagen \n')
    file.write('Fokker periodicity blocks generated by commas: ')

    for comma in commas:
        file.write(str(comma)+ ' ')

    file.write('\n')
    file.write(f'{len(interval_list)}\n!\n')

    for interval in interval_list:
        file.write(str(interval)+'\n')

    file.close()

if __name__ == '__main__':
    sp.init_printing(use_unicode=True)

    include_commas = False
    include_octave = True

    generators = sp.Matrix([[5],[3]])

    comma_positions = sp.Matrix([[-1,4],[-3,0]])

    commas = interval(generators, comma_positions)

    bounding_box = sp.Polygon(sp.Point(0,0), comma_positions.row(0), comma_positions.row(1), comma_positions.row(0) + comma_positions.row(1)).bounds

    interval_list = []

    for i in range(bounding_box[0], bounding_box[1]+1):
        for j in range(bounding_box[2], bounding_box[3]+1):
            pos = sp.Point([i,j])

            if is_in_block(pos, comma_positions, include_commas):
                interval_list.extend(interval(generators, pos))

    interval_list = list(dict.fromkeys(interval_list))
    interval_list.sort(key=float)
    if include_octave:
        interval_list.append('2')

    scl_output('output', commas, interval_list)

